import solution
import exitation
import geometry
import presentation

def run():
    circuit = exitation.build(20, 21, 3, 1/2.55, "gen", Kd=0.0)
    contour = geometry.sample_3_C()
    results = solution.solve(contour, circuit)
    presentation.plot(contour, circuit, results)

# [T, I] = exitation(TIME, T_SIZE, 2, 1/2.55, rlc=True, Kd=0.0)
# [X1, X2, Y1, Y2, Z1, Z2, NC, X, Y, Z, NF] = geometry2I()
# [Bx, By, Bz] = biotsavart3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, X, Y, Z)
# [Fx, Fy, Fz] =     ampere3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, NF)
# plotres2I(TIME, T, I, Bx, By, Bz, Fx, Fy, Fz)


# [T, I] = exitation(TIME, 1, 1, 1/2.55, "const", Kd=0.0)
# [T, I] = exitation(TIME, 21, 1, 1/2.55, "rlc", Kd=0.0)
# [X1, X2, Y1, Y2, Z1, Z2, NC, X, Y, Z, NF] = geometry1L2()
# [Bx, By, Bz] = biotsavart3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, X, Y, Z)
# [Fx, Fy, Fz] =     ampere3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, NF)
# plotres1L2(TIME, T, I, Bx, By, Bz, Fx, Fy, Fz)

# [T, I] = exitation(TIME, 1, 1, 1/2.55, "const", Kd=0.0)
# [T, I] = exitation(TIME, 21, 1, 1/2.55, "rlc", Kd=0.0)
# [X1, X2, Y1, Y2, Z1, Z2, NC, X, Y, Z, NF] = geometry1O()
# [Bx, By, Bz] = biotsavart3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, X, Y, Z)
# [Fx, Fy, Fz] =     ampere3d(X1, X2, Y1, Y2, Z1, Z2, NC, T, I, NF)
# plotres1O(TIME, T, I, Bx, By, Bz, Fx, Fy, Fz)